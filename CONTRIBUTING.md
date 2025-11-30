# Contributing to Educational AI Agent

Thank you for your interest in contributing to this project! We welcome contributions from developers, educators, and anyone passionate about democratizing AI education.

## Code of Conduct

This project is dedicated to providing education to underprivileged learners. We expect all contributors to:
- Be respectful and inclusive
- Focus on the mission of accessible education
- Provide constructive feedback
- Help create a welcoming environment

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Your environment (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! Please:
- Check existing issues first
- Explain the problem it solves
- Describe the proposed solution
- Consider impact on underprivileged users (bandwidth, device capabilities)

### Contributing Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/educational-ai-agent.git
   cd educational-ai-agent
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

4. **Make your changes**
   - Write clear, documented code
   - Follow existing code style
   - Add tests for new features
   - Update documentation

5. **Run tests**
   ```bash
   # Backend tests
   cd backend
   pytest tests/ -v
   
   # Frontend tests
   cd frontend
   npm test
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```
   
   We follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` documentation changes
   - `test:` adding tests
   - `refactor:` code refactoring
   - `style:` formatting changes
   - `chore:` maintenance tasks

7. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

### Code Style

**Python (Backend)**
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Run `black` for formatting: `black .`
- Run `flake8` for linting

**TypeScript/React (Frontend)**
- Use functional components with hooks
- Follow Airbnb style guide
- Use TypeScript for type safety
- Run `npm run lint`

### Testing Guidelines

- Write tests for all new features
- Maintain >80% code coverage
- Test edge cases and error handling
- Mock external API calls
- Include integration tests where appropriate

### Documentation

- Update README.md if needed
- Add docstrings to new functions
- Update API documentation
- Include examples for new features
- Keep documentation accessible (simple language)

## Development Workflow

### Local Development

1. **Start services**
   ```bash
   docker-compose up -d postgres redis
   ```

2. **Run backend**
   ```bash
   cd backend
   python main.py
   ```

3. **Run frontend**
   ```bash
   cd frontend
   npm start
   ```

### With Docker

```bash
docker-compose up --build
```

### Running Tests

```bash
# All tests
docker-compose -f docker-compose.test.yml up

# Backend only
cd backend && pytest

# Frontend only
cd frontend && npm test
```

## Areas for Contribution

### High Priority
- [ ] Multi-language support (Spanish, Hindi, French, etc.)
- [ ] Offline mode for low-connectivity areas
- [ ] Voice interaction for accessibility
- [ ] Mobile responsiveness improvements
- [ ] Performance optimization

### Educational Content
- [ ] New AI topics and curricula
- [ ] Interactive exercises
- [ ] Real-world case studies
- [ ] Video content integration
- [ ] Simplified explanations for complex topics

### Technical Improvements
- [ ] Better error handling
- [ ] Performance monitoring
- [ ] Caching strategies
- [ ] Database optimizations
- [ ] Security enhancements

### Documentation
- [ ] Tutorial videos
- [ ] Teacher guides
- [ ] API documentation
- [ ] Deployment guides
- [ ] Translation of docs

## Community

- **Discussions**: Use GitHub Discussions for questions and ideas
- **Issues**: Use GitHub Issues for bugs and feature requests
- **Email**: eduai-contributors@example.com

## Recognition

Contributors will be:
- Listed in README.md
- Credited in release notes
- Invited to contributor meetings
- Given access to beta features

## Questions?

Feel free to reach out:
- Create a discussion on GitHub
- Email: support@eduai.org
- Join our Discord (link in README)

Thank you for helping make AI education accessible to all!
